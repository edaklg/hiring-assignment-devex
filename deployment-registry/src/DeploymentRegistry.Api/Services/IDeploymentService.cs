using DeploymentRegistry.Api.Models;

namespace DeploymentRegistry.Api.Services;

public interface IDeploymentService
{
    Task<List<Deployment>> GetAsync(string? serviceName, string? environment, string? status);
    Task<Deployment?> GetByIdAsync(string id);
    Task<Deployment> CreateAsync(Deployment deployment);
    Task<Deployment?> UpdateAsync(string id, Deployment deployment);
}
